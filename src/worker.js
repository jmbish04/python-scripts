export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== 'POST' || url.pathname !== '/process') {
      return new Response('Not found', { status: 404 });
    }
    const { input, process, output } = await request.json();
    let text = '';

    if (input.type === 'r2') {
      const obj = await env.R2_BUCKET.get(input.key);
      if (!obj) return new Response('Object not found', { status: 404 });
      text = await obj.text();
    } else if (input.type === 'local') {
      const bytes = Uint8Array.from(atob(input.content), (c) => c.charCodeAt(0));
      text = new TextDecoder().decode(bytes);
    } else if (input.type === 'url') {
      const resp = await fetch(input.url);
      const html = await resp.text();
      text = html.replace(/<[^>]+>/g, ' ');
    }

    const result = { extracted_text: text };

    if (process?.embeddings) {
      result.embedding = text.split(/\s+/).map((t) => t.length);
    }
    if (process?.rag_format) {
      if (process.rag_format === 'json') {
        result.rag = JSON.stringify({ text });
      } else if (process.rag_format === 'markdown') {
        result.rag = `# Extracted Text\n\n${text}`;
      }
    }
    if (process?.summary) {
      result.summary = text.slice(0, 200);
    }

    const prefix = output.key || 'output';
    await env.R2_BUCKET.put(`${prefix}.txt`, text);
    if (result.rag) {
      const ext = process.rag_format === 'json' ? 'json' : 'md';
      await env.R2_BUCKET.put(`${prefix}.rag.${ext}`, result.rag);
    }
    if (result.summary) {
      await env.R2_BUCKET.put(`${prefix}.summary.txt`, result.summary);
    }
    if (result.embedding) {
      await env.R2_BUCKET.put(`${prefix}.embedding.json`, JSON.stringify(result.embedding));
    }

    return new Response(JSON.stringify(result), {
      headers: { 'content-type': 'application/json' },
    });
  },
};

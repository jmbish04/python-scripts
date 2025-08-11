import { Miniflare } from 'miniflare';
import { describe, it, expect } from 'vitest';

const mf = new Miniflare({
  modules: true,
  scriptPath: 'src/worker.js',
  r2Buckets: ['R2_BUCKET']
});

describe('worker', () => {
  it('processes local text', async () => {
    const res = await mf.dispatchFetch('http://localhost/process', {
      method: 'POST',
      body: JSON.stringify({
        input: {
          type: 'local',
          filename: 'a.txt',
          content: Buffer.from('hello world').toString('base64')
        },
        process: { embeddings: true, rag_format: 'json', summary: true },
        output: { key: 'test' }
      })
    });
    const json = await res.json();
    expect(json.extracted_text).toContain('hello');
    expect(json.embedding).toBeTruthy();
    expect(json.rag).toContain('hello');
    expect(json.summary).toBe('hello world');
  });
});

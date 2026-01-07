const fs = require('fs');
const path = require('path');

const filePath = 'corpus.txt';
const minLen = 0;

if (!fs.existsSync(filePath)) {
  console.error('corpus.txt not found');
  process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf8');
const lines = content.split(/\r?\n/).filter(Boolean);

const processChunk = (chunk) => {
  return new Promise((resolve) => {
    const freq = {};
    let total = 0;

    for (const line of chunk) {
      const words = line.split(/\s+/).filter(Boolean);
      total += words.length;

      for (let word of words) {
        word = word.toLowerCase().replace(/[^a-z0-9]/gi, '');
        if (!word || word.length < minLen) continue;
        freq[word] = (freq[word] || 0) + 1;
      }
    }

    resolve({ freq, total });
  });
};

const run = async (concurrency) => {
  const start = process.hrtime.bigint();

  const chunkSize = Math.ceil(lines.length / concurrency);
  const tasks = [];

  for (let i = 0; i < lines.length; i += chunkSize) {
    tasks.push(processChunk(lines.slice(i, i + chunkSize)));
  }

  await Promise.all(tasks);

  const end = process.hrtime.bigint();
  return Number(end - start) / 1_000_000;
};

(async () => {
  const levels = [1, 4, 8];
  const results = [];

  for (const level of levels) {
    console.log(`Running concurrency ${level}`);
    const timeMs = await run(level);
    results.push({ concurrency: level, timeMs });
  }

  if (!fs.existsSync('logs')) {
    fs.mkdirSync('logs', { recursive: true });
  }

  fs.writeFileSync(
    path.join('logs', 'perf-summary.json'),
    JSON.stringify(results, null, 2)
  );

  console.log('Benchmark completed');
})();

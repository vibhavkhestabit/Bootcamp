const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
let filePath = 'corpus.txt';
let topN = 10;
let minLen = 0;
let uniqueOnly = false;
let concurrency = 4; // default parallel chunks

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--file':
      filePath = args[i + 1];
      i++;
      break;
    case '--top':
      topN = parseInt(args[i + 1], 10);
      i++;
      break;
    case '--minLen':
      minLen = parseInt(args[i + 1], 10);
      i++;
      break;
    case '--unique':
      uniqueOnly = true;
      break;
    case '--concurrency':
      concurrency = parseInt(args[i + 1], 10);
      i++;
      break;
    default:
      console.log(`Unknown argument: ${args[i]}`);
  }
}

if (!fs.existsSync(filePath)) {
  console.error(`File not found: ${filePath}`);
  process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf8');
const lines = content.split(/\r?\n/).filter(Boolean);
const chunkSize = Math.ceil(lines.length / concurrency);

const processChunk = (chunk) => {
  return new Promise((resolve) => {
    const frequency = {};
    const uniqueWords = new Set();
    let longest = '';
    let shortest = '';

    for (let line of chunk) {
      const words = line.split(/\s+/).filter(Boolean);
      for (let word of words) {
        word = word.toLowerCase().replace(/[^a-z0-9]/gi, '');
        if (!word) continue;
        if (word.length < minLen) continue;

        if (!longest || word.length > longest.length) longest = word;
        if (!shortest || word.length < shortest.length) shortest = word;

        frequency[word] = (frequency[word] || 0) + 1;
        uniqueWords.add(word);
      }
    }

    resolve({ frequency, uniqueWords, longest, shortest, totalWords: chunk.join(' ').split(/\s+/).length });
  });
};

const chunkPromises = [];
for (let i = 0; i < lines.length; i += chunkSize) {
  chunkPromises.push(processChunk(lines.slice(i, i + chunkSize)));
}

Promise.all(chunkPromises).then((results) => {
  const globalFrequency = {};
  const globalUnique = new Set();
  let globalLongest = '';
  let globalShortest = '';
  let totalWords = 0;

  for (const r of results) {
    totalWords += r.totalWords;
    for (const [word, count] of Object.entries(r.frequency)) {
      globalFrequency[word] = (globalFrequency[word] || 0) + count;
    }
    r.uniqueWords.forEach((w) => globalUnique.add(w));
    if (!globalLongest || r.longest.length > globalLongest.length) globalLongest = r.longest;
    if (!globalShortest || r.shortest.length < globalShortest.length) globalShortest = r.shortest;
  }

  const topWords = Object.entries(globalFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN);

  console.log('Total words:', totalWords);
  console.log('Unique words:', uniqueOnly ? globalUnique.size : globalUnique.size);
  console.log('Longest word:', globalLongest);
  console.log('Shortest word:', globalShortest);

  console.log(`Top ${topN} most frequent words:`);
  for (const [word, count] of topWords) {
    console.log(`${word}: ${count}`);
  }

  const outputDir = 'output';
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const stats = {
    totalWords,
    uniqueWords: globalUnique.size,
    longestWord: globalLongest,
    shortestWord: globalShortest,
    topWords: topWords.map(([word, count]) => ({ word, count }))
  };

  const outputFile = path.join(outputDir, 'stats.json');
  fs.writeFileSync(outputFile, JSON.stringify(stats, null, 2), 'utf8');
  console.log(`\nStats saved to ${outputFile}`);
});

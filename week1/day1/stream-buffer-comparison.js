const fs = require('fs');

function getMemoryUsageMB() {
  return (process.memoryUsage().rss / 1024 / 1024).toFixed(2);
}

// BUFFER METHOD
const bufferStartTime = Date.now();
const bufferStartMemory = getMemoryUsageMB();

fs.readFile('large-file.txt', (err, data) => {
  if (err) throw err;

  const bufferEndTime = Date.now();
  const bufferEndMemory = getMemoryUsageMB();

  const bufferResult = {
    method: 'fs.readFile (Buffer)',
    time_ms: bufferEndTime - bufferStartTime,
    memory_mb: bufferEndMemory
  };

  // STREAM METHOD
  const streamStartTime = Date.now();
  const streamStartMemory = getMemoryUsageMB();

  let totalBytes = 0;
  const stream = fs.createReadStream('large-file.txt');

  stream.on('data', chunk => {
    totalBytes += chunk.length;
  });

  stream.on('end', () => {
    const streamEndTime = Date.now();
    const streamEndMemory = getMemoryUsageMB();

    const streamResult = {
      method: 'fs.createReadStream (Stream)',
      time_ms: streamEndTime - streamStartTime,
      memory_mb: streamEndMemory
    };

    const results = {
      buffer: bufferResult,
      stream: streamResult
    };

    fs.writeFileSync(
      'logs/day1-perf.json',
      JSON.stringify(results, null, 2)
    );

    console.log('Benchmark completed. Results saved to logs/day1-perf.json');
  });
});

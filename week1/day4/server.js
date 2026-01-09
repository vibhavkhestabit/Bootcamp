const http = require('http');
const url = require('url');

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);

  if (parsedUrl.pathname === '/echo') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(req.headers, null, 2));
  }

  else if (parsedUrl.pathname === '/slow') {
    const delay = parseInt(parsedUrl.query.ms) || 1000;
    setTimeout(() => {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(`Response delayed by ${delay} ms`);
    }, delay);
  }

  else if (parsedUrl.pathname === '/cache') {
    res.writeHead(200, {
      'Content-Type': 'text/plain',
      'Cache-Control': 'public, max-age=60',
      'ETag': '"node-cache-123"'
    });
    res.end('Cached response');
  }

  else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});

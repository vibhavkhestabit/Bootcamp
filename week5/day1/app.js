import http from 'http';
console.log("Container started ");
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('Node.js is running inside Docker using ESM!');
});
server.listen(3000, () => {
  console.log('Server listening on port 3000');
});
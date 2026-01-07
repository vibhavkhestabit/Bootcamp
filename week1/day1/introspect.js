const os = require('os');
const { execSync } = require('child_process');

const uptimeSeconds = os.uptime();
const hours = Math.floor(uptimeSeconds / 3600);
const minutes = Math.floor((uptimeSeconds % 3600) / 60);
const seconds = Math.floor(uptimeSeconds % 60);

console.log(`OS: ${os.type()} ${os.release()}`);
console.log(`Architecture: ${os.arch()}`);
console.log(`CPU Cores: ${os.cpus().length}`);
console.log(`Total Memory: ${(os.totalmem() / (1024 ** 3)).toFixed(2)} GB`);
console.log(`System Uptime: ${hours}h ${minutes}m ${seconds}s`);
console.log(`Current Logged User: ${os.userInfo().username}`);
console.log(`Node Path: ${execSync('which node').toString().trim()}`);


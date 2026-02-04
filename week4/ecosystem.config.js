export default {
  apps: [
    {
      name: "product-api-v1",
      script: "./src/index.js",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env_local: {
        environment: "local",
      },
      env_dev: {
        environment: "dev",
      },
      env_prod: {
        environment: "prod",
      }
    }
  ]
};
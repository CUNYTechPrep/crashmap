const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        process.env.REACT_APP_API_PROXY_URL_PREFIX,
        createProxyMiddleware({
            target: process.env.REACT_APP_API_PROXY_TARGET,
            changeOrigin: true
        })
    );
};

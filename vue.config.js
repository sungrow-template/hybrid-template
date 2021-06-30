const path = require('path')

function resolve(dir) {
  return path.join(__dirname, dir)
}

module.exports = {
  publicPath: './',
  devServer: {
    // can be overwritten by process.env.HOST
    host: '0.0.0.0',
    port: 8089
  },
  configureWebpack:{
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 30000,
        maxSize: 0,
        minChunks: 1,
        maxAsyncRequests: 6,
        maxInitialRequests: 4,
        automaticNameDelimiter: '~',
        cacheGroups: {
          vendors: {
            test: /[\\/]node_modules[\\/]/,
            priority: -10,
            chunks: 'initial'
          },
          // 抽离elementUI包
          element: {
            chunks: 'all',
            name: `element-ui`,
            test: /[\\/]element-ui[\\/]/,
            priority: 0,
          },
        }
      }
    }
  },
  chainWebpack: config => {
    // 移除 prefetch 插件
    config.plugins.delete('prefetch')
    // 移除 preload 插件
    config.plugins.delete('preload')
    config.resolve.alias
      .set ('@', resolve ('src'))
      .set ('src', resolve ('src'))
      .set ('common', resolve ('src/common'))
      .set ('_c', resolve ('src/components'))
      .set ('_u', resolve ('src/utils'))
  },
  pluginOptions: {
    electronBuilder: {
      builderOptions: {
        win: {
          // 打包方式,参考https://www.electron.build/configuration/win
          target: [
            {
              'target': 'nsis', // 利用nsis制作安装程序
              'arch': [
                // 'x64', // 64位
                'ia32'// 32位
              ]
            }
          ]
          // icon: './public/app.ico'
        },
        // appId
        appId: 'com.electron.vueCli3Demo',
        // 打包的目录
        extraResources: ['./dist/**'],
        // 打包的名称
        productName: 'vueCli3Demo',
        nsis: {
          // 创建桌面快捷方式： 总是
          createDesktopShortcut: 'always'
        }
      }
    }
  }
}

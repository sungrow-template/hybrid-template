# base-electron-vue-cli3
## 后台目录说明
```
py文件夹放置后台开发时的代码
pydist放置python打包的exe及其他需要内置的文件(会被打包)
```
### python代码打包
```
在py文件夹内包含main.py目录输入命令 pyinstaller -F main.py
```

### python缺少依赖
```
python3 -m pip install 包名
```
pip install -r ../requirements.txt

## 前端项目安装依赖
```
npm install
```

### 前端项目启动
```
npm run dev
```

### 前端electron打包
```
npm run electron:build
```

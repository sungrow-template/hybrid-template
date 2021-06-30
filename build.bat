rmdir /s/q build
rmdir /s/q dist
rmdir /s/q dist_electron
TIMEOUT /T 5 /NOBREAK
pyinstaller py/main.spec
TIMEOUT /T 5 /NOBREAK
npm run electron:build
echo end
pause
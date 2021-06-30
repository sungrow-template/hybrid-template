function toNum(num) {
  var a = num.toString()
  var c = a.split(/\D/)
  var num_place = ['', '0', '00', '000', '0000']
  var r = num_place.reverse()
  for (var i = 0; i < c.length; i++) {
    var len = c[i].length
    c[i] = r[len] + c[i]
  }
  var res = c.join('')
  return res
}
export function comparVersion(oldVer, newVer) {
  const _a = toNum(oldVer)
  const _b = toNum(newVer)
  if (_a === _b) return 0 // 版本一致
  if (_a > _b) return 0 // 当前版本高于发布版本
  if (_a < _b) return 1 // 有新版本
}

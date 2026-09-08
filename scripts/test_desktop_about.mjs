import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const root = new URL('../', import.meta.url);
const require = createRequire(new URL('frontend/package.json', root));
const ts = require('typescript');
const main = fs.readFileSync(new URL('electron/main.js', root),'utf8');
const i18n = fs.readFileSync(new URL('frontend/src/lib/i18n.tsx', root),'utf8');
const ast = ts.createSourceFile('i18n.tsx',i18n,ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX);
let ko;
function visit(n) { if(ts.isVariableDeclaration(n) && n.name.getText(ast)==='KO') ko=Object.fromEntries(n.initializer.properties.filter(ts.isPropertyAssignment).map(p=>[p.name.text,p.initializer.text])); ts.forEachChild(n,visit); }
visit(ast);
const handlers = new Map();const boxes=[];const win={webContents:{},center(){}};
const ctx={ipcMain:{handle:(id,fn)=>handlers.set(id,fn)},mainWindow:win,dialog:{showMessageBox:(_w,opts)=>boxes.push(opts)},app:{getVersion:()=> '1.4.0'}};
vm.createContext(ctx);vm.runInContext(main.slice(main.indexOf('let aboutCopy;'),main.indexOf("ipcMain.handle('window:minimize'")),ctx);
ctx.showAbout();assert.match(boxes.at(-1).detail,/Independently developed/);assert.match(boxes.at(-1).detail,/Prior work for adopted thermal costing/);
const keys={title:'About COMET',description:'Independently developed catalyst manufacturing cost, environmental screening and decision analysis software.',workflow:'Traceable prices, explicit manufacturing boundaries and reproducible comparisons.',priorWork:'Prior work for adopted thermal costing: Baddour et al. (2018); Van Allsburg et al. (2022), CatCost.',button:'OK'};
const korean = Object.fromEntries(Object.entries(keys).map(([k,v])=>{assert.equal(typeof ko[v],'string');return[k,ko[v]];}));
handlers.get('about:set-copy')({sender:win.webContents},korean);ctx.showAbout();assert.equal(boxes.at(-1).title,'COMET 정보');assert.ok(boxes.at(-1).detail.includes(korean.description));assert.ok(boxes.at(-1).detail.includes(korean.priorWork));assert.equal(boxes.at(-1).buttons[0],'확인');
const valid=JSON.stringify(boxes.at(-1));
for(const [sender,copy] of [[{},keys],[win.webContents,null],[win.webContents,{...keys,title:''}],[win.webContents,{...keys,description:'x'.repeat(501)}],[win.webContents,{...keys,priorWork:42}]]) {handlers.get('about:set-copy')({sender},copy);ctx.showAbout();assert.equal(JSON.stringify(boxes.at(-1)),valid);}
handlers.get('about:set-copy')({sender:win.webContents},keys);ctx.showAbout();assert.equal(boxes.at(-1).title,'About COMET');
console.log('About IPC: English fallback, Korean copy, English switch, and 5 invalid sender/payload cases passed.');

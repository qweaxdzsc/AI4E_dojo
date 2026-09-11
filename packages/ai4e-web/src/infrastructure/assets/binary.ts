/** 类型化显示数组解码，身份大整数保持精度。 */
export function decode(bytes:ArrayBuffer,dtype:string):any {
 const types:Record<string,any>={float32:Float32Array,float64:Float64Array,uint8:Uint8Array,int8:Int8Array,uint16:Uint16Array,int16:Int16Array,uint32:Uint32Array,int32:Int32Array,int64:BigInt64Array,uint64:BigUint64Array};
 const Type=types[dtype];if(!Type)throw new Error(`不支持数组类型 ${dtype}`);return new Type(bytes);
}
type Entry={promise:Promise<ArrayBuffer>;bytes:number;used:number;refs:number;controller:AbortController};
const cache=new Map<string,Entry>();const budget=256*1024*1024;
/** 多个窗口持有同一 CPU 缓冲；最后消费者释放即撤销未完下载。 */
export function acquireBuffer(url:string){
 let entry=cache.get(url);
 if(!entry){
  entry={bytes:0,used:Date.now(),refs:0,controller:new AbortController(),promise:Promise.resolve(new ArrayBuffer(0))};const own=entry;
  entry.promise=fetch(url,{signal:entry.controller.signal}).then(async r=>{
   if(!r.ok)throw new Error(await r.text());
   const length=Number(r.headers.get('content-length')||0);if(length>128*1024*1024)throw new Error('显示资产超过预算');
   const data=await r.arrayBuffer();if(data.byteLength>128*1024*1024)throw new Error('显示资产超过预算');
   const total=[...cache.values()].reduce((n,e)=>n+e.bytes,0)+data.byteLength;
   if(total>budget)throw new Error('可视化共享内存超过预算，请关闭其他窗口');
   own.bytes=data.byteLength;return data;
  }).catch(e=>{if(cache.get(url)===own)cache.delete(url);throw e;});cache.set(url,entry);
 }
 entry.refs++;entry.used=Date.now();return entry.promise;
}
export function releaseBuffer(url:string){const entry=cache.get(url);if(!entry)return;entry.refs--;if(entry.refs<=0){entry.controller.abort();cache.delete(url);}}
/** 测试和任务级销毁使用，不能卸载其他活动窗口的数据。 */
export function bufferCacheStats(){return {entries:cache.size,bytes:[...cache.values()].reduce((n,e)=>n+e.bytes,0),references:[...cache.values()].reduce((n,e)=>n+e.refs,0)};}
/** 校验协议摘要、形状和字节序，损坏缓存不能冒充有效数组。 */
export async function decodeBuffer(bytes:ArrayBuffer,descriptor:{dtype:string;shape:number[];byte_length:number;byte_order?:string;sha256?:string}){
 if(bytes.byteLength!==descriptor.byte_length)throw new Error('显示数组字节数不匹配');
 if(descriptor.sha256){const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==descriptor.sha256)throw new Error('显示数组内容摘要不匹配');}
 const type=decode(new ArrayBuffer(0),descriptor.dtype);const size=type.BYTES_PER_ELEMENT;
 if(descriptor.shape.reduce((n,x)=>n*x,1)*size!==bytes.byteLength)throw new Error('显示数组形状不匹配');
 const nativeLittle=new Uint8Array(new Uint16Array([1]).buffer)[0]===1;
 const declared=descriptor.byte_order;
 if(size>1&&declared&&declared!=='not-applicable'&&((declared==='little')!==nativeLittle)){
  const copy=new Uint8Array(bytes.slice(0));for(let i=0;i<copy.length;i+=size)copy.subarray(i,i+size).reverse();return decode(copy.buffer,descriptor.dtype);
 }
 return decode(bytes,descriptor.dtype);
}

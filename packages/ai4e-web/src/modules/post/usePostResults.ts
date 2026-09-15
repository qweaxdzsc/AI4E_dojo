import {useCallback,useEffect,useRef,useState} from 'react';
import {resultCatalog} from './api';
import type {ResultCatalog} from './model';
/** 刷新目录保留页面选择，迟到响应不能跨任务覆盖；不拉结果文件树。 */
export function usePostResults(project:string,task:string){
 const [catalog,setCatalog]=useState<ResultCatalog>({items:[],files:[],batches:[],errors:[],total:0}),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const generation=useRef(0);
 const refresh=useCallback(async()=>{const n=++generation.current;setBusy(true);try{const value=await resultCatalog(project,task);if(n===generation.current){setCatalog({...value,files:value.files||[]});setError('');}}catch(e){if(n===generation.current)setError((e as Error).message);}finally{if(n===generation.current)setBusy(false);}},[project,task]);
 useEffect(()=>{void refresh();const update=()=>void refresh();window.addEventListener('dojo:task-updated',update);return()=>{generation.current++;window.removeEventListener('dojo:task-updated',update);};},[refresh]);
 return {catalog,busy,error,refresh};
}

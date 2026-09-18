/** 输出表单只对支持透明通道的图片格式提交透明请求。 */
import {render, screen, fireEvent, cleanup} from '@testing-library/react';
import {afterEach, expect, test, vi} from 'vitest';
import {AnimationExportDialog} from '../modules/visPhysField/components/AnimationExportDialog';
afterEach(cleanup);
test('PNG 显式开启透明背景后传给导出请求',()=>{
 const submit=vi.fn();
 render(<AnimationExportDialog open animation={false} onExport={submit}/>);
 fireEvent.click(screen.getByRole('checkbox',{name:'透明背景'}));
 fireEvent.click(screen.getByRole('button',{name:'生 成'}));
 expect(submit.mock.calls[0][0]).toMatchObject({format:'png',transparent_background:true});
});
test('MP4 不显示透明选项且请求为不透明',()=>{
 const submit=vi.fn();
 render(<AnimationExportDialog open animation times={[0,1]} onExport={submit}/>);
 expect(screen.queryByRole('checkbox',{name:'透明背景'})).toBeNull();
 fireEvent.click(screen.getByRole('button',{name:'生 成'}));
 expect(submit.mock.calls[0][0]).toMatchObject({format:'mp4',transparent_background:false});
});

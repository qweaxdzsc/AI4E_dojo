/** 三维物理场统一视口容器；具体面板由二级业务组件提供。 */

import styles from './PhysFieldViewport.module.css';

/** 渲染共享视口挂载点，不自行创建Trame连接。 */
export default function PhysFieldViewport({ children, title = '三维物理场' }) {
  return <section className={styles.viewport} aria-label={title}><div className={styles.canvas}>{children}</div></section>;
}

export default function PageTitle({ title, description, actions, meta }) {
  return (
    <header className="page-title-row">
      <div>
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
        {meta ? <div className="page-title-meta">{meta}</div> : null}
      </div>
      {actions ? <div className="page-title-actions">{actions}</div> : null}
    </header>
  );
}

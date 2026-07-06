type JsonViewerProps = {
  data: unknown;
  className?: string;
  maxHeight?: string;
};

export function JsonViewer({
  data,
  className = '',
  maxHeight = '24rem',
}: JsonViewerProps) {
  const formatted = JSON.stringify(data, null, 2);

  return (
    <div
      className={`overflow-hidden rounded-xl border border-border bg-surface-soft ${className}`}
    >
      <pre
        className="overflow-auto p-4 text-xs leading-relaxed text-graphite"
        style={{ maxHeight }}
      >
        <code className="whitespace-pre-wrap break-words font-mono">
          {formatted}
        </code>
      </pre>
    </div>
  );
}

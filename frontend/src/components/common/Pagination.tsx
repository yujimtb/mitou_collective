import Link from "next/link";

export function Pagination({
  currentPage,
  perPage,
  totalCount,
  basePath,
  query,
}: {
  currentPage: number;
  perPage: number;
  totalCount: number;
  basePath: string;
  query: Record<string, string | undefined>;
}) {
  const totalPages = Math.max(1, Math.ceil(totalCount / perPage));
  const createHref = (page: number) => {
    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      }
    });
    params.set("page", String(page));
    return `${basePath}?${params.toString()}`;
  };

  return (
    <div className="pagination">
      <p className="supporting-text" style={{ margin: 0 }}>
        Page {currentPage} of {totalPages}
      </p>
      <div className="actions-row">
        {currentPage > 1 ? (
          <Link className="ghost-button" href={createHref(currentPage - 1)}>
            Previous
          </Link>
        ) : null}
        {currentPage < totalPages ? (
          <Link className="button" href={createHref(currentPage + 1)}>
            Next
          </Link>
        ) : null}
      </div>
    </div>
  );
}

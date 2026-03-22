export function SearchBar({
  query,
  entityType,
}: {
  query: string;
  entityType: string;
}) {
  return (
    <form className="filter-bar search-bar" method="get">
      <label style={{ flex: "2 1 280px" }}>
        Search
        <input defaultValue={query} name="q" placeholder="entropy, compression, horizon..." />
      </label>

      <label>
        Entity type
        <select defaultValue={entityType} name="type">
          <option value="all">All entities</option>
          <option value="claim">Claims only</option>
          <option value="concept">Concepts only</option>
          <option value="term">Terms only</option>
          <option value="context">Contexts only</option>
          <option value="evidence">Evidence only</option>
        </select>
      </label>

      <button className="button" type="submit">
        Search
      </button>
    </form>
  );
}

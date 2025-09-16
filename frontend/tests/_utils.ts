// frontend/tests/_utils.ts
export function pickList(json: any): any[] {
  if (Array.isArray(json)) return json;
  if (Array.isArray(json?.result)) return json.result;
  if (Array.isArray(json?.items)) return json.items;
  return [];
}

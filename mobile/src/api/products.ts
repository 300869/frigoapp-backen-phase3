// src/api/products.ts
import api from "./client";

export type ProductDto = {
  id: number | string;
  name: string;
  location: "fridge" | "freezer" | "pantry";
  quantity: number;
  expiry_date?: string | null;
  days_to_expire?: number | null;
};

export type ProductsResp = {
  items: ProductDto[];
  total?: number;
  page?: number;
  size?: number;
};

export async function listProducts(params?: { page?: number; size?: number; search?: string; location?: string }) {
  const { data } = await api.get<ProductsResp | ProductDto[]>("/products", { params });
  // Supporte 2 formats: {items:[...]} ou [...]
  const items = Array.isArray(data) ? data : data.items;
  return items;
}

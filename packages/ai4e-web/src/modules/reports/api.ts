import { request } from "../../infrastructure/http/client";
export const read = (p: string) => request("/projects/" + p + "/report");
export const save = (p: string, v: unknown) =>
  request("/projects/" + p + "/report", v, "PUT");

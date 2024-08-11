import { Highlight, Content } from "react-pdf-highlighter-extended";

export interface ResultHighlight extends Highlight {
  content: Content;
  similarity: number;
}

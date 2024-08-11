import React from "react";
import type { ViewportHighlight } from "react-pdf-highlighter-extended";

import "./style/HighlightPopup.css";
import { ResultHighlight } from "./types";

interface HighlightPopupProps {
  highlight: ViewportHighlight<ResultHighlight>;
}

const HighlightPopup = ({ highlight }: HighlightPopupProps) => {
  return highlight.id ? (
    <div className="Highlight__popup">Similarity score : {highlight.similarity.toFixed(3)}</div>
  ) : (
    null
  );
};

export default HighlightPopup;

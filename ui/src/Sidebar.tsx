import React, { useContext, useRef } from "react";
import type { Highlight } from "react-pdf-highlighter-extended";
import "./style/Sidebar.css";
import Search from "./Search";
import { AppContext } from "./App";
import { VList } from "virtua";

const updateHash = (highlight: Highlight) => {
  document.location.hash = `highlight-${highlight.id}`;
};

const Sidebar = () => {
  const { highlights, rowcount } = useContext(AppContext);
  const sidebarRef = useRef<HTMLDivElement>(null);

  const onSearchClick = (targetElement: HTMLDivElement | null) => {

    setTimeout(() => {
      if (sidebarRef.current && targetElement) {
        const offsetTop = targetElement.offsetTop;
        sidebarRef.current.scrollTo({
          top: offsetTop,
          behavior: 'smooth',
        });
      }
    }, 500);
  };

  return (
    <div className="sidebar" style={{ width: "25vw", maxWidth: "500px" }} ref={sidebarRef}>
      <div className="description" style={{ padding: "1rem" }}>
        <h2 style={{ marginBottom: "1rem" }}>
          Intra-search
        </h2>
        <p>
          Search within documents semantically.
        </p>
      </div>
      <Search onSearchClick={onSearchClick} />
      <h4 style={{ marginLeft: "1rem" }}>Results</h4>
      <VList style={{ height: "500px" }}>
        {(highlights?.length > 0) ? (
          highlights.slice(0, rowcount).map((highlight, index) => (
            <div
              key={index}
              className="sidebar__highlight"
              onClick={() => {
                updateHash(highlight);
              }}
            >
              <div>
                {/* Highlighted text */}
                {highlight.content.text && (
                  <blockquote style={{ marginTop: "0.5rem" }} title={highlight.content.text}>
                    {`${highlight.content.text.slice(0, 90).trim()}…`}
                  </blockquote>
                )}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                {/* Highlight page number */}
                <span className="highlight__location">
                  Page {highlight.position.boundingRect.pageNumber}
                </span>
                {/* Text similarity */}
                <span className="highlight__similarity" title={`Similarity Score = ${highlight.similarity.toFixed(3)}`}>
                  {highlight.similarity.toFixed(3)}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: "center", fontSize: "0.8rem" }}>No Results Found</div>
        )}
      </VList>
    </div>
  );
};

export default Sidebar;

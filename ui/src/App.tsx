import React, { createContext, useCallback, useEffect, useRef, useState } from "react";
import HighlightContainer from "./HighlightContainer";
import Sidebar from "./Sidebar";
import Selector from "./Selector";
import {
  PdfHighlighter,
  PdfHighlighterUtils,
  PdfLoader,
} from "react-pdf-highlighter-extended";
import "./style/App.css";
import { ResultHighlight } from "./types";
import { BASE_URL } from "./config";


const parseIdFromHash = () => {
  return document.location.hash.slice("#highlight-".length);
};

const resetHash = () => {
  document.location.hash = "";
};

interface Context {
  highlights: Array<ResultHighlight>;
  setHighlights: React.Dispatch<Array<ResultHighlight>>;
  embeddingId: string;
  setEmbeddingId: React.Dispatch<string>;
  rowcount: number;
  setRowcount: React.Dispatch<number>;
}

export const AppContext = createContext<Context>({ highlights: [], setHighlights: () => { }, embeddingId: "", setEmbeddingId: () => { }, rowcount: 0, setRowcount: () => { } });

const App = () => {
  const [embeddingId, setEmbeddingId] = useState('');
  const [rowcount, setRowcount] = useState(0);
  const [highlights, setHighlights] = useState<Array<ResultHighlight>>([]);

  // Refs for PdfHighlighter utilities
  const highlighterUtilsRef = useRef<PdfHighlighterUtils>();

  const getHighlightById = useCallback((id: string) => {
    return highlights.find((highlight) => highlight.id === id);
  }, [highlights]);


  useEffect(() => {
    history.pushState("#", document.title, window.location.pathname + window.location.search);
  }, []);

  const resetHighlights = () => {
    setHighlights([]);
    setRowcount(0);
  };

  // Scroll to highlight based on hash in the URL
  const scrollToHighlightFromHash = useCallback(() => {
    const highlight = getHighlightById(parseIdFromHash());
    if (highlight && highlighterUtilsRef.current) {
      highlighterUtilsRef.current.scrollToHighlight(highlight);
    }
  }, [getHighlightById]);

  // Hash listeners for autoscrolling to highlights
  useEffect(() => {
    window.addEventListener("hashchange", scrollToHighlightFromHash);

    return () => {
      window.removeEventListener("hashchange", scrollToHighlightFromHash);
    };
  }, [scrollToHighlightFromHash]);

  return (
    <AppContext.Provider value={{ highlights, setHighlights, embeddingId, setEmbeddingId, rowcount, setRowcount, }}>
      <div className="App" style={{ display: "flex", height: "100vh" }}>
        <Sidebar />
        <div
          style={{
            height: "100vh",
            width: "75vw",
            overflow: "hidden",
            position: "relative",
            flexGrow: 1,
          }}
        >
          <Selector
            resetHighlights={resetHighlights}
          />
          {embeddingId != "" && <PdfLoader document={`${BASE_URL}/api/doc/${embeddingId}`}>
            {(pdfDocument) => (
              <PdfHighlighter
                enableAreaSelection={(event) => event.altKey}
                pdfDocument={pdfDocument}
                onScrollAway={resetHash}
                utilsRef={(_pdfHighlighterUtils) => {
                  highlighterUtilsRef.current = _pdfHighlighterUtils;
                }}
                textSelectionColor={"rgba(255, 226, 143, 1)"}
                highlights={highlights.slice(0, rowcount)}
                style={{
                  height: "calc(100% - 41px)",
                }}
              >
                <HighlightContainer editHighlight={() => { }} />
              </PdfHighlighter>
            )}
          </PdfLoader>}
        </div>

      </div>
    </AppContext.Provider>
  );
};

export default App;

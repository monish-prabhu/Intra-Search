import React, { useContext, useState, useEffect, useRef } from 'react';
import './style/search.css';
import { AppContext } from './App';
import { BASE_URL } from './config';

interface SearchProps {
    onSearchClick: (targetElement: HTMLDivElement | null) => void;
}

const Search: React.FC<SearchProps> = ({ onSearchClick }) => {
    const [query, setQuery] = useState("");
    const [count, setCount] = useState(0);
    const [isButtonEnabled, setIsButtonEnabled] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const { setHighlights, setRowcount, embeddingId, highlights } = useContext(AppContext);
    const maxResultsRef = useRef<HTMLDivElement>(null); // Ref for "Max Results" div

    useEffect(() => {
        // Reset query and result count when embeddingId changes
        setQuery("");
        setCount(0);

    }, [embeddingId]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value);

    const handleCount = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCount(Number(e.target.value));
        setIsButtonEnabled(true);
    };

    const handleFilter = () => {
        setRowcount(count);
        setIsButtonEnabled(false);
    };

    const handleSubmit = async () => {
        if (!embeddingId) {
            window.alert("Select a document before searching!");
        } else if (!query) {
            window.alert("Query must not be empty!");
        } else {
            setIsLoading(true);
            try {
                const response: Response = await fetch(`${BASE_URL}/api/${embeddingId}/query?query=${query}`);
                const results = await response.json();
                setHighlights(results);

                // Default: Show top 10 query results
                const minCount = Math.min(10, results.length);
                setCount(minCount);
                setRowcount(minCount);

                // Smooth scroll to Results section
                onSearchClick(maxResultsRef.current);
            } catch (err) {
                window.alert("Unable to process query!");
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <div className='search-container'>
            <textarea
                id="search"
                name="search"
                placeholder="Type your query here ..."
                value={query}
                onChange={handleChange}
            />
            <button
                className='search-button'
                onClick={handleSubmit}
                disabled={isLoading} // Disable button while loading
            >
                {isLoading ? "Searching" : "Search"}
            </button>

            <div ref={maxResultsRef}>Max Results: {count}</div>
            <input
                type="range"
                min={0}
                max={highlights.length}
                value={count}
                step={1}
                onChange={handleCount}
            />
            <button disabled={!isButtonEnabled} onClick={handleFilter} style={{ height: "25px" }}>Filter</button>
        </div>
    );
};

export default Search;

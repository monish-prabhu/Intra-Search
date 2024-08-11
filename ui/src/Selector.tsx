import React, { useContext, useEffect, useState } from 'react';
import Select, { SingleValue, StylesConfig } from "react-select";
import { AppContext } from './App';
import { BASE_URL } from './config';

interface Option {
    chunk_size: number;
    document_name: string;
    model: string;
    id: string;
}

const formatOptionLabel = ({ chunk_size, document_name, model }: Option) => (
    <div style={{ display: "flex", flexDirection: "column", rowGap: "0.5rem" }}>
        <div>{document_name}</div>
        <div style={{ display: "flex", color: "#616161", justifyContent: "space-between" }}>
            <div>
                {`Model: ${model}`}
            </div>
            <div>
                {`Chunk size: ${chunk_size}`}
            </div>
        </div>
    </div>
);

interface SelectorProps {
    resetHighlights: () => void;
}

const Selector: React.FC<SelectorProps> = ({ resetHighlights }) => {

    const { setEmbeddingId } = useContext(AppContext);
    const [options, setOptions] = useState<Option[]>([]);

    const handleChange = (option: SingleValue<Option>) => {
        if (option) {
            resetHighlights();
            setEmbeddingId(option.id);
        }
    };

    const styles: StylesConfig<Option, false> = {
        container: (base) => ({
            ...base,
            flex: 1,
        }),
        menu: (provided) => ({
            ...provided,
            zIndex: 9999,
        }),
        menuList: (styles) => {
            return {
                ...styles,
                maxHeight: 200,
            };
        }
    };

    const customFilterOption = (option: { data: Option }, searchText: string) => {
        const searchValue = searchText.toLowerCase();
        return (
            String(option.data.chunk_size).includes(searchValue) ||
            option.data.document_name.toLowerCase().includes(searchValue) ||
            option.data.model.toLowerCase().includes(searchValue) ||
            option.data.id.toLowerCase().includes(searchValue)
        );
    };

    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const result: Response = await fetch(`${BASE_URL}/api/embeddings`);
                setOptions(await result.json());
            } catch (e) {
                window.alert(`Unable to fetch embedding info!`);
            }
        };
        fetchOptions();
    }, []);

    return (
        <div style={{ display: "flex", justifyContent: "center", padding: "1rem 1rem 1rem" }}>
            <Select
                defaultValue={options?.[0]}
                formatOptionLabel={formatOptionLabel}
                options={options}
                styles={styles}
                getOptionValue={(option) => option.id}
                filterOption={customFilterOption}
                onChange={handleChange}
            />
        </div>
    );
}

export default Selector;

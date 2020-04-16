import React, { useState, useEffect, useCallback, forwardRef } from 'react';
import $ from 'jquery';
import queryString from 'query-string';
import './PlaceholderItem.scss';
import { Semaphore } from 'await-semaphore';

// Limit concurrent requests for resolving placeholder items
const MAX_CONCURRENT_REQUESTS = 3;
const semaphore = new Semaphore(MAX_CONCURRENT_REQUESTS);

async function fetchData({ worksheetUUID, directive }) {
    return semaphore.use(async () => {
        const queryParams = {
            directive,
        };
        const info = await $.ajax({
            type: 'GET',
            url:
                '/rest/interpret/worksheet/' +
                worksheetUUID +
                '?' +
                queryString.stringify(queryParams),
            async: true,
            dataType: 'json',
            cache: false,
        });
        return info;
    });
}

export default forwardRef((props, ref) => {
    const [item, setItem] = useState(undefined);
    const [error, setError] = useState(false);
    const { worksheetUUID, onAsyncItemLoad } = props;
    const { directive } = props.item;
    useEffect(() => {
        (async function() {
            try {
                const { items } = await fetchData({ directive, worksheetUUID });
                setItem(items.length === 0 ? null : items[0]);
                // onAsyncItemLoadCallback();
            } catch (e) {
                console.error(e);
                setError(e);
            }
        })();
    }, [directive, worksheetUUID]);
    if (error) {
        return <div ref={ref}>Error loading item.</div>;
    }
    if (item === null) {
        // No items
        return <div ref={ref}>No results found.</div>;
    }
    return <div ref={ref} className='codalab-item-placeholder'></div>;
});

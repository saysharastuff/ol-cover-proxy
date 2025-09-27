from fastapi import FastAPI, Query
import requests
import random
import logging
from typing import List, Dict, Any, Optional

app = FastAPI()

OPENLIBRARY_BOOK_URL = "https://openlibrary.org/books/{}.json"
OPENLIBRARY_AUTHOR_URL = "https://openlibrary.org{}.json"
COVER_URL = "https://covers.openlibrary.org/b/olid/{}-L.jpg"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_json(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch JSON data from a given URL.

    Args:
        url (str): The URL to fetch data from.

    Returns:
        Optional[Dict[str, Any]]: The JSON data if the request is successful, None otherwise.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        return None


def fetch_book_data(work_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch book data from OpenLibrary using the work ID.

    Args:
        work_id (str): The OpenLibrary work ID.

    Returns:
        Optional[Dict[str, Any]]: The book data if the request is successful, None otherwise.
    """
    return fetch_json(OPENLIBRARY_BOOK_URL.format(work_id))


def fetch_author_names(authors: List[Dict[str, Any]]) -> List[str]:
    """
    Fetch author names from a list of author data.

    Args:
        authors (List[Dict[str, Any]]): A list of author data.

    Returns:
        List[str]: A list of author names.
    """
    author_names = []
    for author in authors:
        author_key = author.get("key")
        if author_key:
            author_data = fetch_json(OPENLIBRARY_AUTHOR_URL.format(author_key))
            if author_data:
                author_names.append(author_data.get("name"))
    return author_names


def get_cover_image(work_id: str, covers: List[int]) -> Optional[str]:
    """
    Get the cover image URL for a book.

    Args:
        work_id (str): The OpenLibrary work ID.
        covers (List[int]): A list of cover IDs.

    Returns:
        Optional[str]: The cover image URL if covers are available, None otherwise.
    """
    return COVER_URL.format(work_id) if covers else None


def fetch_work_data_from_book(book_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Fetch work data from a book data.

    Args:
        book_data (Dict[str, Any]): The book data.

    Returns:
        Optional[Dict[str, Any]]: The work data if available, None otherwise.
    """
    works = book_data.get("works", [])
    if works:
        work_key = works[0].get("key")
        if work_key:
            return fetch_json(f"https://openlibrary.org{work_key}.json")
    return None


def parse_description(description_data: Any) -> str:
    """
    Parse the description data to extract the description value.

    Args:
        description_data (Any): The description data.

    Returns:
        str: The parsed description.
    """
    if isinstance(description_data, dict):
        return description_data.get("value", "")
    return description_data or ""


def extract_tags(book_data: Dict[str, Any], work_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Extract tags from book data and work data.

    Args:
        book_data (Dict[str, Any]): The book data.
        work_data (Optional[Dict[str, Any]]): The work data.

    Returns:
        str: A comma-separated list of tags.
    """
    tags = set()
    for key in [
            "subjects", "subject_places", "subject_people", "subject_times"
    ]:
        tags.update(book_data.get(key, []))
    if work_data:
        for key in [
                "subjects", "subject_places", "subject_people",
                "subject_times", "genres"
        ]:
            tags.update(work_data.get(key, []))
    tag_list = list(tags)

    return ', '.join(tag_list)


@app.get("/import")
@app.get("/import/")
async def get_random_book(work_ids: str = Query(
    ..., description="Comma-separated OpenLibrary work IDs")):
    """
    Get a random book from a list of OpenLibrary work IDs.

    Args:
        work_ids (str): Comma-separated OpenLibrary work IDs.

    Returns:
        Dict[str, Any]: A dictionary containing book data.
    """
    ids = work_ids.split(",")
    attempts = 3

    while attempts > 0:
        work_id = random.choice(ids)
        book_data = fetch_book_data(work_id)

        if book_data:
            try:
                covers = book_data.get("covers", [])
                cover_image = get_cover_image(work_id, covers)
                authors_list = fetch_author_names(book_data.get("authors", []))

                description = parse_description(book_data.get("description"))

                # Try to get work-level fallback data
                work_data = fetch_work_data_from_book(book_data)
                if not description and work_data:
                    description = parse_description(work_data.get("description"))

                tags = extract_tags(book_data, work_data)
                url = f"https://openlibrary.org/works/{work_id}"

                return {
                    "work_id": work_id,
                    "title": book_data.get("title"),
                    "authors": authors_list,
                    "description": description,
                    "covers": covers,
                    "cover_image": cover_image,
                    "tags": tags,
                    "url": url
                }
            except Exception as e:
                logger.error(f"Error processing book data for work_id {work_id}: {e}")
                attempts -= 1
                continue
        attempts -= 1

    return {"message": "Add valid open library ids in your plugin settings"}

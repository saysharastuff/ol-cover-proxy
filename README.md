# OpenLibrary Cover Proxy

This project provides endpoints to query the OpenLibrary API for a random book from a list of work IDs. It is designed to be used as a proxy for the [TRMNL app](https://usetrmnl.com), Book by it's Cover.

## Features

- Fetch book data and cover images from OpenLibrary
- Return random book data from a list of work IDs

## Setup

1. Clone the repository
2. Install dependencies: `pip install fastapi requests`
3. Run the application: `fastapi run`

## Usage

- Send a GET request to `/import` with a comma-separated list of OpenLibrary work IDs as a query parameter.
- Example: `http://localhost:8000/import?work_ids=OL25954563M,OL34928346M`

## API Response

The API returns a JSON object with the following fields:

- `work_id`: The OpenLibrary work ID
- `title`: The book title
- `authors`: A list of author names
- `description`: The book description
- `covers`: A list of cover IDs
- `cover_image`: The URL of the cover image
- `tags`: A comma-separated list of tags
- `url`: The URL of the book on OpenLibrary

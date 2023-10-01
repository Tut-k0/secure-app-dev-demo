from fastapi import Depends, APIRouter, HTTPException, Response
from pyodbc import Cursor

from app.database import get_db
from app.schemas import ListingCreate, Listing, ListingUpdate

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("/", response_model=Listing)
async def create_listing(listing_data: ListingCreate, db: Cursor = Depends(get_db)):
    # Insert new listing.
    insert_query = """
        INSERT INTO listings (title, description, price, seller_id)
        values (?, ?, ?, ?);
        """
    db.execute(
        insert_query,
        listing_data.title,
        listing_data.description,
        listing_data.price,
        listing_data.seller_id,
    )

    db.commit()

    # Retrieve the highest ascending ID matching by title or description.
    select_query = """
                SELECT MAX(listing_id)
                FROM listings
                WHERE title = ? OR description = ?;
                """
    db.execute(select_query, listing_data.title, listing_data.description)
    listing_id = db.fetchone()[0]
    # Preparing output object.
    listing = vars(listing_data)
    listing["listing_id"] = listing_id

    return listing


@router.get("/{listing_id}", response_model=Listing)
async def get_listing(listing_id: int, db: Cursor = Depends(get_db)):
    l = db.execute("SELECT * FROM listings WHERE listing_id = ?;", listing_id).fetchone()
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    return Listing(
        listing_id=l.listing_id,
        title=l.title,
        description=l.description,
        price=l.price,
        seller_id=l.seller_id,
    )


@router.get("/", response_model=list[Listing])
async def get_listings(keyword: str | None = None, db: Cursor = Depends(get_db)):
    if keyword:
        # Use a parameterized query to avoid SQL injection
        query = """
                SELECT * FROM listings
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY listing_id;
            """
        # Prepare the search pattern (including '%' wildcard) for the parameter
        keyword_pattern = f"%{keyword}%"

        db.execute(query, (keyword_pattern, keyword_pattern))
    else:
        query = "SELECT * FROM listings ORDER BY listing_id;"
        db.execute(query)

    cols = [column[0] for column in db.description]
    listings = db.fetchall()

    return [Listing(**dict(zip(cols, row))) for row in listings]


@router.put("/{listing_id}", response_model=Listing)
async def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    db: Cursor = Depends(get_db),
):
    existing_listing = db.execute(
        "SELECT * FROM listings WHERE listing_id = ?;", listing_id
    ).fetchone()
    if not existing_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Update the listing data
    update_query = """
        UPDATE listings
        SET title = ?, description = ?, price = ?
        WHERE listing_id = ?;
        """
    db.execute(
        update_query,
        listing_data.title,
        listing_data.description,
        listing_data.price,
        listing_id,
    )
    db.commit()

    # Return the updated listing
    updated_listing = Listing(
        listing_id=listing_id,
        title=listing_data.title,
        description=listing_data.description,
        price=listing_data.price,
        seller_id=existing_listing.seller_id,  # Seller ID remains unchanged
    )
    return updated_listing


@router.delete("/{listing_id}", response_model=Listing)
async def delete_listing(
    listing_id: int,
    db: Cursor = Depends(get_db),
):
    # Check if the listing exists
    existing_listing = db.execute(
        "SELECT * FROM listings WHERE listing_id = ?;", listing_id
    ).fetchone()
    if not existing_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Delete the listing
    db.execute("DELETE FROM listings WHERE listing_id = ?;", listing_id)
    db.commit()

    return Response(status_code=204)

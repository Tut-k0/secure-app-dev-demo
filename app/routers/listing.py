from fastapi import Depends, APIRouter, HTTPException
from pyodbc import Cursor

from app.database import get_db
from app.schemas import ListingCreate, Listing

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("/", response_model=Listing)
async def create_listing(listing_data: ListingCreate, db: Cursor = Depends(get_db)):
    # Insert new listing.
    db.execute(
        """
        INSERT INTO listings (title, description, price, seller_id)
        values ('%s', '%s', %f, %d);
        """
        % (listing_data.title, listing_data.description, listing_data.price, listing_data.seller_id)
    )
    db.commit()
    # Return the new listing id.
    db.execute("SELECT SCOPE_IDENTITY() AS listing_id;")
    listing_id = db.fetchone().listing_id
    # Preparing output object.
    listing = vars(listing_data)
    listing["listing_id"] = listing_id

    return listing


@router.get("/{listing_id}", response_model=Listing)
async def get_listing(listing_id: int, db: Cursor = Depends(get_db)):
    l = db.execute("SELECT * FROM listings WHERE listing_id = %d;" % listing_id).fetchone()
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
        query = f"""
                SELECT * FROM listings
                WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'
                ORDER BY listing_id;
                """
    else:
        query = "SELECT * FROM listings ORDER BY listing_id;"

    db.execute(query)
    cols = [column[0] for column in db.description]
    listings = db.fetchall()

    return [Listing(**dict(zip(cols, row))) for row in listings]

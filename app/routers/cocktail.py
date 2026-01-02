from fastapi import APIRouter, HTTPException
from app.utils.cocktail_service import (
    fetch_cocktail_list,
    fetch_cocktail_detail,
    fetch_cocktails_by_letter
)

router = APIRouter(
    prefix="/api/cocktails",
    tags=["Cocktails"]
)

@router.get("/")
async def list_cocktails(name: str):
    """
    List cocktails by name
    """
    try:
        return await fetch_cocktail_list(name)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch cocktail list"
        )

@router.get("/{cocktail_id}")
async def cocktail_detail(cocktail_id: str):
    """
    Get cocktail detail by ID
    """
    try:
        return await fetch_cocktail_detail(cocktail_id)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch cocktail detail"
        )


@router.get("/by-letter/{letter}")
async def cocktails_by_letter(letter: str):
    """
    List cocktails by first letter (a-z)
    """
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(
            status_code=400,
            detail="Letter must be a single alphabet character (a-z)"
        )

    try:
        return await fetch_cocktails_by_letter(letter.lower())
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch cocktails by letter"
        )
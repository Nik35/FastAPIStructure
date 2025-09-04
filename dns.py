from fastapi import APIRouter, HTTPException

router = APIRouter()

# Dynamic router for handling multiple versions
@router.api_route("/{version}/dns/create", methods=["POST"])
async def create_dns(version: str):
    if version == "v1":
        return {"message": "DNS create endpoint for v1"}
    elif version == "v2":
        return {"message": "DNS create endpoint for v2"}
    else:
        raise HTTPException(status_code=404, detail="API version not supported")

@router.api_route("/{version}/dns/read", methods=["GET"])
async def read_dns(version: str):
    if version == "v1":
        return {"message": "DNS read endpoint for v1"}
    elif version == "v2":
        return {"message": "DNS read endpoint for v2"}
    else:
        raise HTTPException(status_code=404, detail="API version not supported")

# Example to add more endpoints dynamically
@router.api_route("/{version}/dns/delete", methods=["DELETE"])
async def delete_dns(version: str):
    if version == "v1":
        return {"message": "DNS delete endpoint for v1"}
    elif version == "v2":
        return {"message": "DNS delete endpoint for v2"}
    else:
        raise HTTPException(status_code=404, detail="API version not supported")

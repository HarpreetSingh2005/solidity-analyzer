// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe NFT marketplace escrow enforcing pull-over-push.
contract SafeMarketplace {
    struct Listing {
        address seller;
        uint256 price;
        bool isActive;
    }

    mapping(uint256 => Listing) public listings;
    mapping(address => uint256) public pendingWithdrawals;

    event Listed(uint256 indexed tokenId, uint256 price, address seller);
    event Sold(uint256 indexed tokenId, uint256 price, address buyer);

    function listToken(uint256 tokenId, uint256 price) external {
        require(price > 0, "Price must be greater than zero");
        
        listings[tokenId] = Listing({
            seller: msg.sender,
            price: price,
            isActive: true
        });

        emit Listed(tokenId, price, msg.sender);
    }

    function buyToken(uint256 tokenId) external payable {
        Listing storage listing = listings[tokenId];
        require(listing.isActive, "Listing not active");
        require(msg.value == listing.price, "Incorrect value sent");

        listing.isActive = false;
        
        // Push pattern: update balance instead of direct transfer
        pendingWithdrawals[listing.seller] += msg.value;

        emit Sold(tokenId, listing.price, msg.sender);
    }

    function withdraw() external {
        uint256 amount = pendingWithdrawals[msg.sender];
        require(amount > 0, "No pending funds");

        pendingWithdrawals[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
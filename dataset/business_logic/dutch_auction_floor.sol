// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Dutch Auction Price Floor Bypass
 * CATEGORY: Business Logic — Missing Floor Enforcement in Price Decay
 *
 * The Dutch auction price decays linearly from startPrice to 0 over
 * auctionDuration. There is no floor price — if nobody bids for long
 * enough, price reaches 0 and the NFT can be bought for free.
 * Additionally, the auction can be extended by the owner who also
 * participates, creating a front-running opportunity.
 */
contract DutchAuctionFloor {
    address public owner;
    uint256 public startPrice;
    uint256 public floorPrice;    // declared but never enforced!
    uint256 public startTime;
    uint256 public auctionDuration;
    address public winner;
    bool    public settled;

    constructor(uint256 _start, uint256 _floor, uint256 _duration) {
        owner           = msg.sender;
        startPrice      = _start;
        floorPrice      = _floor;   // BUG: stored but ignored in currentPrice()
        startTime       = block.timestamp;
        auctionDuration = _duration;
    }

    function currentPrice() public view returns (uint256) {
        if (block.timestamp >= startTime + auctionDuration) return 0; // BUG: should be floorPrice
        uint256 elapsed = block.timestamp - startTime;
        // BUG: linear decay to 0 — floor never applied
        return startPrice - (startPrice * elapsed / auctionDuration);
    }

    function bid() external payable {
        require(!settled, "Auction settled");
        uint256 price = currentPrice();
        require(msg.value >= price, "Bid too low");
        winner   = msg.sender;
        settled  = true;
        // BUG: refund overflow — if price=0, entire msg.value kept by contract
        uint256 refund = msg.value - price;
        if (refund > 0) payable(msg.sender).transfer(refund);
        payable(owner).transfer(price);
    }

    // BUG: owner can delay auction to rebid at a lower price
    function extendAuction(uint256 extra) external {
        require(msg.sender == owner, "Not owner");
        auctionDuration += extra;
    }
}

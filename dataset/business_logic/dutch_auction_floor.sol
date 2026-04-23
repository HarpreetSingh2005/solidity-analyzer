// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract DutchAuctionFloor {
    uint256 public startPrice = 1 ether;
    uint256 public floorPrice = 0.1 ether;
    uint256 public startTime;
    uint256 public duration = 1 days;
    function currentPrice() public view returns (uint256) {
        uint256 elapsed = block.timestamp - startTime;
        if (elapsed >= duration) return 0; // BUG: should be floorPrice
        return startPrice - (startPrice * elapsed / duration);
    }
}
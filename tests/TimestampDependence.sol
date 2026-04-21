// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Test contract for Timestamp Dependence detection
contract TimestampDependence {
    address public owner;
    uint256 public auctionEnd;
    address public highestBidder;
    uint256 public highestBid;

    constructor(uint256 _duration) {
        owner = msg.sender;
        // BUG: using block.timestamp sets a manipulable deadline
        auctionEnd = block.timestamp + _duration;
    }

    // VULNERABLE: auction outcome depends on block.timestamp
    function bid() public payable {
        // BUG: miner can manipulate block.timestamp ~15 seconds
        require(block.timestamp < auctionEnd, "Auction ended");
        require(msg.value > highestBid, "Bid too low");

        if (highestBidder != address(0)) {
            payable(highestBidder).transfer(highestBid);
        }
        highestBidder = msg.sender;
        highestBid = msg.value;
    }

    // VULNERABLE: winner determined purely by timestamp
    function claimPrize() public {
        require(block.timestamp >= auctionEnd, "Auction not ended");
        require(msg.sender == highestBidder, "Not the winner");
        payable(msg.sender).transfer(address(this).balance);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnAuctionDoS {
    address public highestBidder;
    uint256 public highestBid;

    // Vulnerability: Push payment can DoS the auction if previous bidder is a contract that reverts
    function bid() external payable {
        require(msg.value > highestBid, "Bid too low");

        if (highestBidder != address(0)) {
            // If this fails, the whole transaction reverts
            (bool success, ) = highestBidder.call{value: highestBid}("");
            require(success, "Refund failed");
        }

        highestBidder = msg.sender;
        highestBid = msg.value;
    }
}
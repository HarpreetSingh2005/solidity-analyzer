// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Push over pull in auction. Prevents new bids if current highest bidder rejects ETH.
contract VulnNewAuctionSnipe {
    address public highestBidder;
    uint256 public highestBid;
    function bid() external payable {
        require(msg.value > highestBid, "Too low");
        if (highestBidder != address(0)) {
            (bool success, ) = highestBidder.call{value: highestBid}("");
            require(success, "Refund failed"); // Reverts if receiver is a non-payable contract
        }
        highestBidder = msg.sender;
        highestBid = msg.value;
    }
}
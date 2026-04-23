// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Single centralized address can arbitrarily change the price, creating a huge rug-pull risk.
contract VulnNewOracleCentralized {
    uint256 public price;
    address public owner;
    function updatePrice(uint256 _price) external {
        require(msg.sender == owner, "Only owner");
        price = _price;
    }
}
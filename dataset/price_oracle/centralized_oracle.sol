// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract CentralizedOracle {
    address public owner;
    uint256 public price;
    constructor() { owner = msg.sender; }
    function setPrice(uint256 _price) external {
        require(msg.sender == owner);
        price = _price; // BUG: single point of failure
    }
}
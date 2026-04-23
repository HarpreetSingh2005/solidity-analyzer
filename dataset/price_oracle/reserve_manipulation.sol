// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract ReserveManipulation {
    uint256 public reserve0;
    uint256 public reserve1;
    function getPrice() public view returns (uint256) {
        return (reserve1 * 1e18) / reserve0; // BUG: live reserves manipulatable
    }
}
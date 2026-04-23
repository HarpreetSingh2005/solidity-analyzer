// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract ManipulatedReserve {
    uint256 public reserve;
    function setReserve(uint256 r) external {
        reserve = r; // BUG: manipulatable reserve
    }
}
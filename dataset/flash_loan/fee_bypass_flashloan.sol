// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract FeeBypassFlashloan {
    function deposit() external payable {}
    function withdraw() external {
        // BUG: fee bypass via flash loan
    }
}
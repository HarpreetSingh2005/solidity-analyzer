// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Parent {
    uint256 public value = 10;
}

contract Shadowing is Parent {
    // Vulnerable: shadows 'value' from Parent
    uint256 public value = 20;

    function getValue() public view returns (uint256) {
        return value; // which one? (Shadowing.value)
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeNFTMinter {
    mapping(uint256 => address) public ownerOf;
    uint256 public totalSupply;

    function mint() public {
        totalSupply++;
        ownerOf[totalSupply] = msg.sender;
    }
}
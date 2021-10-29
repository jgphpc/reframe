#include <iostream>

int main() {
   // Test that basic arithmetics still work:
   if( 1 + 1 == 2 ) {
      std::cout << "Yes" << std::endl;
      return 0;
   } else {
      std::cout << "No" << std::endl;
      return 1;
   }
}
